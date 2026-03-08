import { useEffect, createRef } from "react";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { DefaultPluginUISpec, PluginUISpec } from "molstar/lib/mol-plugin-ui/spec";
import { PluginSpec } from "molstar/lib/mol-plugin/spec";
import { MolViewSpec } from 'molstar/lib/extensions/mvs/behavior';
import "molstar/lib/mol-plugin-ui/skin/light.scss";
import { MAQualityAssessment } from "molstar/lib/extensions/model-archive/quality-assessment/behavior";

declare global {
    interface Window {
        molstar?: PluginUIContext;
    }
}

interface MolStarWrapperProps {
    setMolStar: (molstar: PluginUIContext) => void;
}


export function MolStarWrapper({ setMolStar }: MolStarWrapperProps) {
    const parent = createRef<HTMLDivElement>();

    useEffect(() => {
        async function init() {
            const defaultSpecs = DefaultPluginUISpec();
            const specs: PluginUISpec = {
                behaviors: [...defaultSpecs.behaviors, PluginSpec.Behavior(MolViewSpec), PluginSpec.Behavior(MAQualityAssessment)],
                components: {
                    ...defaultSpecs.components,
                    remoteState: "none",
                },

                layout: {
                    initial: {
                        isExpanded: false,
                        showControls: false,
                        regionState: {
                            bottom: "full",
                            left: "full",
                            right: "full",
                            top: "full",
                        },
                    },
                },
            };

            window.molstar = await createPluginUI({
                target: parent.current as HTMLDivElement,
                spec: specs,
                render: renderReact18
            });
            setMolStar(window.molstar)

        }
        init();
        return () => {
            window.molstar?.dispose();
            window.molstar = undefined;
        };
    }, []);

    return <div ref={parent} style={{ width: 640, height: 480 }}/>;
}
