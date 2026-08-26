import type { Plugin } from '@opencode-ai/plugin';
/**
 * A model reference in `provider/model-id` form, e.g. `zai/glm-4.7`.
 */
export type ModelRef = string;
/** Minimal slice of opencode's merged config that we mutate. */
interface ConfigLike {
    provider?: Record<string, {
        models?: Record<string, {
            name?: string;
        } & Record<string, unknown>>;
        [k: string]: unknown;
    }>;
    agent?: Record<string, {
        model?: string;
        [k: string]: unknown;
    }>;
}
export interface ModeModelOptions {
    /** Model pinned to plan mode, e.g. `zai/glm-5.2`. */
    plan?: ModelRef;
    /** Model pinned to build mode, e.g. `zai/glm-4.7`. */
    build?: ModelRef;
}
/**
 * For a user-defined (custom) provider, ensure the model id is declared so
 * opencode can route to it. No-ops for built-in/catalog providers, which are
 * already known. This is what fixes the silent-fallback-after-restart case.
 */
export declare function ensureRegistered(cfg: ConfigLike, ref: ModelRef): boolean;
/**
 * Pin models to the built-in `plan` and `build` agents and ensure both models
 * resolve. Returns the subset that was actually applied.
 */
export declare function applyModeModels(cfg: ConfigLike, opts: ModeModelOptions): ModeModelOptions;
/**
 * Pins a model to each opencode mode (plan / build) and keeps it pinned across
 * restarts. Configure via the `OPENCODE_PLAN_MODEL` / `OPENCODE_BUILD_MODEL`
 * environment variables, each in `provider/model-id` form.
 */
declare const ModeModel: Plugin;
export default ModeModel;
export { ModeModel };
