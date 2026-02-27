import { Box, HStack, Link, Switch, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import { getCompStruct, ComputedStructure } from "../api/computed_structure"
import { resultDetailRoute } from "../Router";
import MolStarWrapper, { MolStarWrapperModel } from "../components/MolStarWrapper";
import MotifDetail from "../components/MotifDetail";
import { useEffect, useState } from "react";
import { loadMVS, MVSData } from "molstar/lib/extensions/mvs";
import { useQuery } from "@tanstack/react-query";


// function getSugarResult(_abrev: string, afId: string): ComputedStructure | undefined {
//     return resultsList.find(r => r.afid === afId) 
// }


function ResultDetail() {
    const { afId } = resultDetailRoute.useParams()

    const { data: compStruct, isLoading, isError, error } = useQuery<ComputedStructure, Error>({
        queryKey: ["comp-struct"],
        queryFn: () => getCompStruct(afId)
    });



    const [molstar, setMolstar] = useState<MolStarWrapperModel|undefined>(undefined)


    useEffect(() => {
        if (!molstar) return

            const mvsBuilder = MVSData.createBuilder()
            mvsBuilder
                .download({ url: `https://models.rcsb.org/af_afo25142f1.bcif` })
                .parse({ format: 'bcif' })
                .modelStructure({})
                .component({})
                .representation({})
                .color({ color: "blue" })
            const mvsData = mvsBuilder.getState();

            // const response = await fetch('https://raw.githubusercontent.com/molstar/molstar/master/examples/mvs/1cbs.mvsj');
            // const rawData = await response.text();
            // const mvsData: MVSData = MVSData.fromMVSJ(rawData);


            loadMVS(molstar.plugin, mvsData, { sourceUrl: undefined, sanityChecks: true, replaceExisting: false });
        

    }, [molstar])

    if (compStruct === undefined) {
        return (
            <MainContainer>
                <Box >Unknow AlphaFold ID</Box>
            </MainContainer>
        )
    }

    if (isLoading) return <div>Loading computed structure...</div>;
    if (isError) return <div>Error: {error.message}</div>;


    return (
        <MainContainer>
            <VStack width="100%" alignItems="flex-start" mt="3">
                <Box fontWeight="bold" fontSize="3xl">{compStruct.title}</Box>
                <HStack width="100%" alignItems="flex-start" spacing="10">
                    <Box>
                        <TableContainer>
                            <Table variant="striped" colorScheme="whiteAlpha" size="sm">
                                <Tbody>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">AlphaFold DB:</Td>
                                        <Td>
                                            <Link href={`https://alphafold.ebi.ac.uk/entry/${compStruct.afdb_id.split("-")[1]}`}>
                                                {compStruct.afdb_id}
                                            </Link>
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">UniProtKB:</Td>
                                        <Td>
                                            <Link href={`https://www.uniprot.org/uniprotkb/${compStruct.afdb_id.split("-")[1]}`}>
                                                {`${compStruct.afdb_id.split("-")[1]}`}
                                            </Link>
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">pLDDT (global)</Td>
                                        <Td>
                                            {compStruct.plddt}
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Organism:</Td>
                                        <Td>
                                            {compStruct.organism}
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Total number of found motifs:</Td>
                                        <Td>
                                            {compStruct.motifs.length}
                                        </Td>
                                    </Tr>
                                </Tbody>
                            </Table>
                        </TableContainer>
                        <VStack mt="3"> {/*FIXME: use query information*/}
                            {compStruct.motifs.map((m, i) => <MotifDetail num={i} sugar={m.sugar} rmsd={m.score} residues="" structurePDB={m.original_structure} />)}
                        </VStack>
                    </Box>
                    <VStack flexGrow="1">
                        <Box position="relative" width="100%" zIndex="10">
                            <MolStarWrapper setMolstar={setMolstar}/>
                        </Box>
                        <Switch></Switch>
                    </VStack>
                </HStack>
            </VStack>
        </MainContainer>
    )
}

export default ResultDetail
