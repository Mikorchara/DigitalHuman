/**
 * Copyright(c) Live2D Inc. All rights reserved.
 *
 * Use of this source code is governed by the Live2D Open Software license
 * that can be found at https://www.live2d.com/eula/live2d-open-software-license-agreement_en.html.
 */

import { LAppDelegate } from './lappdelegate';
import * as LAppDefine from './lappdefine';
import { CubismFramework } from '@framework/live2dcubismframework';

/**
 * ブラウザロード後の処理
 */
window.addEventListener(
  'load',
  (): void => {
    // Initialize WebGL and create the application instance
    if (!LAppDelegate.getInstance().initialize()) {
      return;
    }

    LAppDelegate.getInstance().run();

    // Expose global API for external control (Python bridge / custom JS)
    let _lipSyncTimer: number | null = null;
    let _speechInterval: number | null = null;

    // Helper: resolve model instance
    const getModel = () => {
      const delegate = LAppDelegate.getInstance();
      const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
      return mgr?.getModel(0) ?? null;
    };

    // Stop any running speech lip sync
    const stopSpeech = () => {
      if (_speechInterval !== null) {
        clearTimeout(_speechInterval);
        _speechInterval = null;
      }
      if (_lipSyncTimer !== null) {
        clearTimeout(_lipSyncTimer);
        _lipSyncTimer = null;
      }
      const m = getModel();
      if (m) m.stopManualLipSync();
    };

    (window as any).Live2D = {
      // Play a specific motion by group name and index
      playMotion(group: string, no: number, priority?: number) {
        const delegate = LAppDelegate.getInstance();
        const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
        const model = mgr?.getModel(0);
        if (!model) return;
        model.startMotion(
          group, no,
          priority ?? LAppDefine.PriorityForce,
        );
      },
      // Play random motion from group
      playRandomMotion(group: string, priority?: number) {
        const delegate = LAppDelegate.getInstance();
        const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
        const model = mgr?.getModel(0);
        if (!model) return;
        model.startRandomMotion(
          group,
          priority ?? LAppDefine.PriorityForce,
        );
      },
      // Set expression by ID
      setExpression(exprId: string) {
        const delegate = LAppDelegate.getInstance();
        const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
        const model = mgr?.getModel(0);
        if (!model) return;
        model.setExpression(exprId);
      },
      // Toggle auto idle motion (true = loop rand idle, false = freeze)
      setAutoIdle(enabled: boolean) {
        const delegate = LAppDelegate.getInstance();
        const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
        const model = mgr?.getModel(0);
        if (!model) return;
        model.setAutoIdle(enabled);
        console.log('[Live2D.setAutoIdle] ' + enabled);
      },
      // Directly set a parameter once (may be overwritten by updaters)
      setParameter(paramId: string, value: number) {
        const delegate = LAppDelegate.getInstance();
        const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
        const model = mgr?.getModel(0);
        const cubismModel = model?.getModel();
        if (!cubismModel) return;
        const idHandle = CubismFramework.getIdManager().getId(paramId);
        cubismModel.setParameterValueById(idHandle, value);
      },
      // Keep a parameter at a value (re-applies every frame via interval)
      holdParameter(paramId: string, value: number, intervalMs: number = 30) {
        const idHandle = CubismFramework.getIdManager().getId(paramId);
        const apply = () => {
          const delegate = LAppDelegate.getInstance();
          const mgr = delegate.getSubdelegate(0)?.getLive2DManager();
          const model = mgr?.getModel(0);
          const cubismModel = model?.getModel();
          if (!cubismModel) return;
          cubismModel.setParameterValueById(idHandle, value);
        };
        apply();
        return setInterval(apply, intervalMs);
      },
      // Natural speech lip sync: multi-phoneme mouth shapes
      // text: the reply content (used to count syllable slots)
      // durationMs: total speaking duration in ms (MUST match TTS audio length)
      startSpeechLipSync(text: string, durationMs: number = 5000) {
        stopSpeech();

        const model = getModel();
        if (!model) return;

        console.log('[Live2D.speech] starting, text=' + text.length + ' chars, dur=' + durationMs + 'ms');

        // ----- Phoneme mouth shapes (ParamMouthForm, ParamMouthOpenY) -----
        const phonemes: Array<[number, number]> = [
          [-1.2, 1.0],  // wide open "a"
          [0.6,  0.65], // round "o"
          [-0.3, 0.45], // slight open "i/e"
          [0.0,  0.8],  // neutral open
          [-0.6, 0.55], // half-wide
        ];

        const CLOSED: [number, number] = [1.0, 0.0];

        // Count speakable characters (skip whitespace, treat punctuation as chars too)
        const chars = [...text].filter(ch => ch.trim());
        const charCount = Math.max(chars.length, 3);

        // Evenly divide total duration among all characters — NO separate pauses
        const baseInterval = Math.round(durationMs / charCount);
        const interval = Math.max(80, Math.min(250, baseInterval));

        let lastPhoneme = -1;
        let cycleCount = 0;
        let charIndex = 0;

        const pickPhoneme = (): [number, number] => {
          let idx = Math.floor(Math.random() * phonemes.length);
          if (phonemes.length > 1 && idx === lastPhoneme) {
            idx = (idx + 1 + Math.floor(Math.random() * (phonemes.length - 1))) % phonemes.length;
          }
          lastPhoneme = idx;
          const [bForm, bOpen] = phonemes[idx];
          const fj = (Math.random() - 0.5) * 0.3;
          const oj = (Math.random() - 0.5) * 0.2;
          return [bForm + fj, Math.min(1.0, bOpen + oj)];
        };

        const tick = () => {
          if (_lipSyncTimer === null && _speechInterval === null) return;

          if (charIndex >= charCount) {
            model.startManualLipSync(CLOSED[0], CLOSED[1]);
            return;
          }

          charIndex++;
          const [form, open] = pickPhoneme();
          model.startManualLipSync(form, open);
          cycleCount++;

          const jitter = Math.round((Math.random() - 0.5) * 40);
          const nextDelay = Math.max(50, interval + jitter);
          _speechInterval = window.setTimeout(tick, nextDelay);
        };

        model.startManualLipSync(CLOSED[0], CLOSED[1]);
        _speechInterval = window.setTimeout(tick, interval);

        _lipSyncTimer = window.setTimeout(() => {
          console.log('[Live2D.speech] stopping after ' + cycleCount + ' cycles');
          stopSpeech();
        }, durationMs);
      },

      // Stop speech lip sync immediately
      stopLipSync() {
        stopSpeech();
      },
    };

    console.log('[Live2D] Global API exposed: window.Live2D');
  },
  { passive: true }
);

/**
 * 終了時の処理
 */
window.addEventListener(
  'beforeunload',
  (): void => LAppDelegate.releaseInstance(),
  { passive: true }
);
