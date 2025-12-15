// import { Box } from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { PluginUIContext } from "molstar/lib/commonjs/mol-plugin-ui/context";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { loadMVS, MVSData } from "molstar/lib/commonjs/extensions/mvs";
import { MAQualityAssessment, MAQualityAssessmentConfig, QualityAssessmentPLDDTPreset, QualityAssessmentQmeanPreset } from 'molstar/lib/commonjs/extensions/model-archive/quality-assessment/behavior';
import { QualityAssessment } from 'molstar/lib/commonjs/extensions/model-archive/quality-assessment/prop';
import { SbNcbrPartialCharges, SbNcbrPartialChargesPreset, SbNcbrPartialChargesPropertyProvider, SbNcbrTunnels } from 'molstar/lib/commonjs/extensions/sb-ncbr';
import { PresetStructureRepresentations } from 'molstar/lib/mol-plugin-state/builder/structure/representation-preset';
import { StateObjectRef, StateObjectSelector } from 'molstar/lib/mol-state';
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import "molstar/lib/mol-plugin-ui/skin/light.scss";
import { DefaultPluginUISpec } from "molstar/lib/mol-plugin-ui/spec";
import { Box } from "@chakra-ui/react";
import { PluginSpec } from "molstar/lib/mol-plugin/spec";
import { MolViewSpec } from 'molstar/lib/extensions/mvs/behavior';
import { StructureRepresentationPresetProvider } from "molstar/lib/mol-plugin-state/builder/structure/representation-preset";
import { PluginConfig } from "molstar/lib/mol-plugin/config";
// import { PluginConfigItem } from "molstar/lib/mol-plugin/config";
// import "../assets/light.scss"

// function MolStarWrapper() {
//     const containerRef = useRef(null);
//     const [ viewer, setViewer ] = useState(null)
//
//     useEffect(() => {
//         if (containerRef.current) {
//             // const builder = molstar.PluginExtensions.mvs.MVSData.createBuilder();
//             // const structure = builder
//             //     .download({ url: `https://models.rcsb.org/af_afo25142f1.bcif` })
//             //     .parse({ format: 'bcif' })
//             //     .modelStructure({})
//             //     .component({})
//             //     .representation({})
//             //     .color({ color: "blue" });
//             // const mvsData = builder.getState();
//
//             const v = new Viewer(containerRef.current);
//             setViewer(v)
//
//             // viewer.create(containerRef.current, { layoutIsExpanded: false, layoutShowControls: false })
//             //     .then(viewer => molstar.PluginExtensions.mvs.loadMVS(viewer.plugin, mvsData, { sourceUrl: undefined, sanityChecks: true, replaceExisting: false }));
//             //
//
//         }
//     }, []);
//
// }
//
//

export function MolStarWrapper() {
    const parent = useRef<HTMLDivElement>(null);

    const [ viewer, setViewer ] = useState<PluginUIContext|null>(null)

    useEffect(() => {
        async function init() {
            if (viewer === null) {
                const defaultSpecs = DefaultPluginUISpec();
                const molstar = await createPluginUI({
                    target: parent.current as HTMLDivElement,
                    render: renderReact18,
                    spec: {
                        actions: defaultSpecs.actions,
                        behaviors: [
                            ...defaultSpecs.behaviors,
                            PluginSpec.Behavior(MolViewSpec)
                        ],
                        components: {
                            ...defaultSpecs.components,
                        },
                        layout: {
                            initial: {
                                isExpanded: false,
                                showControls: false,
                            }
                        },
                        config: [
                            [PluginConfig.Structure.DefaultRepresentationPreset, ViewerAutoPreset.id],
                        ]
                    }
                });

                const mvsBuilder = MVSData.createBuilder()
                mvsBuilder
                    .download({ url: `https://models.rcsb.org/af_afo25142f1.bcif` })
                    .parse({ format: 'bcif' })
                    .modelStructure({})
                    .component({})
                    .representation({})
                    .color({ color: "blue" });
                const mvsData = mvsBuilder.getState();

                // const response = await fetch('https://raw.githubusercontent.com/molstar/molstar/master/examples/mvs/1cbs.mvsj');
                // const rawData = await response.text();
                // const mvsData: MVSData = MVSData.fromMVSJ(rawData);


                await loadMVS(molstar, mvsData);

                console.log("molstar", molstar)

                // //@ts-ignore
                setViewer(molstar)
                console.log("viewer", viewer)
            }

        }
        init().then(() => console.log("molstar created", viewer));
        // return () => {
        //     viewer?.dispose();
        //     setViewer(null);
        // };
    }, []);

    // setTimeout(async () => {
    //     console.log(viewer)
    //         const response = await fetch('https://raw.githubusercontent.com/molstar/molstar/master/examples/mvs/1cbs.mvsj');
    //         const rawData = await response.text();
    //         const mvsData: MVSData = MVSData.fromMVSJ(rawData);
    //         await loadMVS(viewer, mvsData);
    // }, 2000);

    // return <div ref={parent} style={{ width: 640, height: 480 }}/>;
    return <Box ref={parent} border="1px" width="70%" height="30em"></Box>
}



// export type MolstarViewerProps = {
//   plugin: PluginUIContext;
// } & HTMLAttributes<HTMLElement>;
//
// export const MolstarViewer = ({
//   plugin,
//   className,
//   ...props
// }: MolstarViewerProps) => {
//
//   return (
//     <Box {...props} >
//       <div className="w-full h-full relative">
//         <Plugin plugin={plugin} />
//       </div>
//     </Box>
//   );
// };


const ViewerAutoPreset = StructureRepresentationPresetProvider({
    id: 'preset-structure-representation-viewer-auto',
    display: {
        name: 'Automatic (w/ Annotation)', group: 'Annotation',
        description: 'Show standard automatic representation but colored by quality assessment (if available in the model).'
    },
    isApplicable(a) {
        return (
            !!a.data.models.some(m => QualityAssessment.isApplicable(m, 'pLDDT')) ||
            !!a.data.models.some(m => QualityAssessment.isApplicable(m, 'qmean'))
        );
    },
    params: () => StructureRepresentationPresetProvider.CommonParams,
    async apply(ref, params, plugin) {
        const structureCell = StateObjectRef.resolveAndCheck(plugin.state.data, ref);
        const structure = structureCell?.obj?.data;
        if (!structureCell || !structure) return {};

        if (!!structure.models.some(m => QualityAssessment.isApplicable(m, 'pLDDT'))) {
            return await QualityAssessmentPLDDTPreset.apply(ref, params, plugin);
        } else if (!!structure.models.some(m => QualityAssessment.isApplicable(m, 'qmean'))) {
            return await QualityAssessmentQmeanPreset.apply(ref, params, plugin);
        } else if (!!structure.models.some(m => SbNcbrPartialChargesPropertyProvider.isApplicable(m))) {
            return await SbNcbrPartialChargesPreset.apply(ref, params, plugin);
        } else {
            return await PresetStructureRepresentations.auto.apply(ref, params, plugin);
        }
    }
});

export default MolStarWrapper
