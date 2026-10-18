function parse(ref) {
    const idx = ref.indexOf('/');
    if (idx <= 0 || idx >= ref.length - 1)
        return null;
    return { provider: ref.slice(0, idx), id: ref.slice(idx + 1) };
}
/**
 * For a user-defined (custom) provider, ensure the model id is declared so
 * opencode can route to it. No-ops for built-in/catalog providers, which are
 * already known. This is what fixes the silent-fallback-after-restart case.
 */
export function ensureRegistered(cfg, ref) {
    const parsed = parse(ref);
    if (!parsed)
        return false;
    const provider = cfg.provider?.[parsed.provider];
    if (!provider)
        return false;
    provider.models = provider.models ?? {};
    if (!provider.models[parsed.id])
        provider.models[parsed.id] = { name: parsed.id };
    return true;
}
/**
 * Pin models to the built-in `plan` and `build` agents and ensure both models
 * resolve. Returns the subset that was actually applied.
 */
export function applyModeModels(cfg, opts) {
    const applied = {};
    cfg.agent = cfg.agent ?? {};
    if (opts.build) {
        ensureRegistered(cfg, opts.build);
        cfg.agent.build = cfg.agent.build ?? {};
        cfg.agent.build.model = opts.build;
        applied.build = opts.build;
    }
    if (opts.plan) {
        ensureRegistered(cfg, opts.plan);
        cfg.agent.plan = cfg.agent.plan ?? {};
        cfg.agent.plan.model = opts.plan;
        applied.plan = opts.plan;
    }
    return applied;
}
function fromEnv() {
    return {
        plan: process.env.OPENCODE_PLAN_MODEL,
        build: process.env.OPENCODE_BUILD_MODEL,
    };
}
/**
 * Pins a model to each opencode mode (plan / build) and keeps it pinned across
 * restarts. Configure via the `OPENCODE_PLAN_MODEL` / `OPENCODE_BUILD_MODEL`
 * environment variables, each in `provider/model-id` form.
 */
const ModeModel = async () => {
    return {
        config: async (cfg) => {
            const opts = fromEnv();
            if (!opts.plan && !opts.build)
                return;
            applyModeModels(cfg, opts);
        },
    };
};
export default ModeModel;
export { ModeModel };
