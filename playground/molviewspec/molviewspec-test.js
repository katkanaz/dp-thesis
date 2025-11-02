const builder = molstar.PluginExtensions.mvs.MVSData.createBuilder();
const structure = builder
    .download({ url: "https://models.rcsb.org/af_afa0a175w077f1.bcif" })
    .parse({ format: 'bcif' })
    .modelStructure({})
    .component({})
    .representation({})
    .color({ color: "blue" });
const mvsData = builder.getState();

molstar.Viewer.create("viewer1", { layoutIsExpanded: false, layoutShowControls: false })
    .then(viewer => molstar.PluginExtensions.mvs.loadMVS(viewer.plugin, mvsData, { sourceUrl: undefined, sanityChecks: true, replaceExisting: false }));
