console.log(searchResults);

const containerOuter = document.getElementById("container-outer");

function renderViewers(surroundingId) {
    const viewerList = document.querySelectorAll(`.molviewspec-${surroundingId}`)
    console.log(viewerList)
    for (const viewer of viewerList) {
        const builder = molstar.PluginExtensions.mvs.MVSData.createBuilder();
        const structure = builder
            .download({ url: `https://models.rcsb.org/${viewer.getAttribute("data-computed-model-id").toLowerCase()}.bcif` })
            .parse({ format: 'bcif' })
            .modelStructure({})
            .component({})
            .representation({})
            .color({ color: "blue" });
        const mvsData = builder.getState();

        molstar.Viewer.create(viewer, { layoutIsExpanded: false, layoutShowControls: false })
            .then(viewer => molstar.PluginExtensions.mvs.loadMVS(viewer.plugin, mvsData, { sourceUrl: undefined, sanityChecks: true, replaceExisting: false }));
    }

}

for (const representativeSurrounding in searchResults) {
    const detailEl = document.createElement("details");
    const summaryEl = document.createElement("summary");
    summaryEl.addEventListener("click", () => renderViewers(representativeSurrounding))


    const summaryDiv = document.createElement("div");
    summaryDiv.style.display = "inline-flex";
    summaryDiv.style.justifyContent = "space-between";
    summaryDiv.style.width = "95%"

    const surroundingNameDiv = document.createElement("div"); 
    surroundingNameDiv.appendChild(document.createTextNode(representativeSurrounding));
    summaryDiv.appendChild(surroundingNameDiv);

    const numFoundDiv = document.createElement("div"); 
    numFoundDiv.appendChild(document.createTextNode(`${Object.keys(searchResults[representativeSurrounding]).length} found`));
    summaryDiv.appendChild(numFoundDiv);

    summaryEl.appendChild(summaryDiv);


    detailEl.appendChild(summaryEl);


    const computedModelCardContainer = document.createElement("div");

    for (const computedModelId in searchResults[representativeSurrounding]) {
        const computedModelCard = document.createElement("div");
        computedModelCard.style.display = "flex"
        computedModelCard.style.gap = "1em"
        const computedModelCardLeft = document.createElement("div");
        const computedModelCardRight = document.createElement("div");

        const computedModelName = document.createElement("div");
        computedModelName.appendChild(document.createTextNode(computedModelId));
        const computedModelTitle = document.createElement("div");
        computedModelTitle.appendChild(document.createTextNode(searchResults[representativeSurrounding][computedModelId][0]));
        const computedModelKeyWords = document.createElement("div");
        computedModelKeyWords.appendChild(document.createTextNode(searchResults[representativeSurrounding][computedModelId][1]));

        computedModelCard.appendChild(computedModelCardLeft);
        computedModelCard.appendChild(computedModelCardRight);

        computedModelCardRight.appendChild(computedModelName);
        computedModelCardRight.appendChild(computedModelTitle);
        computedModelCardRight.appendChild(computedModelKeyWords);

        const molViewSpecDiv = document.createElement("div");
        molViewSpecDiv.style.width = "300px";
        molViewSpecDiv.style.height = "300px";
        molViewSpecDiv.style.position = "relative";
        molViewSpecDiv.classList.add(`molviewspec-${representativeSurrounding}`)
        molViewSpecDiv.setAttribute("data-computed-model-id", computedModelId)

        
        computedModelCardLeft.appendChild(molViewSpecDiv);


        computedModelCardContainer.appendChild(computedModelCard);
    }

    detailEl.appendChild(computedModelCardContainer);

    containerOuter.appendChild(detailEl);
}
