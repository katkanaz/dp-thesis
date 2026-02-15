import { Box, HStack, Link, Switch, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import type { ResultInfo } from "../components/SearchResultItem"
import { resultsList } from "./SugarResults"
import { resultDetailRoute } from "../Router";
import MolStarWrapper, { MolStarWrapperModel } from "../components/MolStarWrapper";
import MotifDetail from "../components/MotifDetail";
import { useEffect, useState } from "react";
import { loadMVS, MVSData } from "molstar/lib/extensions/mvs";


function getSugarResult(_abrev: string, afId: string): ResultInfo | undefined {
    return resultsList.find(r => r.afid === afId) 
}


function ResultDetail() {
    const { abrev, afId } = resultDetailRoute.useParams()

    const [molstar, setMolstar] = useState<MolStarWrapperModel|undefined>(undefined)

    const result = getSugarResult(abrev, afId)
    if (result === undefined) {
        return (
            <MainContainer>
                <Box >Unknow AlphaFold ID</Box>
            </MainContainer>
        )
    }

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

    return (
        <MainContainer>
            <VStack width="100%" alignItems="flex-start" mt="3">
                <Box fontWeight="bold" fontSize="3xl">{result.title}</Box>
                <HStack width="100%" alignItems="flex-start" spacing="10">
                    <Box>
                        <TableContainer>
                            <Table variant="striped" colorScheme="whiteAlpha" size="sm">
                                <Tbody>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">AlphaFold DB:</Td>
                                        <Td>
                                            <Link>
                                                {result.afid}
                                            </Link>
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">UniProtKB:</Td>
                                        <Td>
                                            <Link>
                                                {result.uniprotid}
                                            </Link>
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">pLDDT (global)</Td>
                                        <Td>
                                            89.94
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Organism:</Td>
                                        <Td>
                                            Helicobacter pylori 26695
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Total number of found motifs:</Td>
                                        <Td>
                                            2
                                        </Td>
                                    </Tr>
                                </Tbody>
                            </Table>
                        </TableContainer>
                        <VStack mt="3">
                            <MotifDetail num={1} sugar="FUC" rmsd="0.1 Å" residues="TRP: A-7, GLN: A-9, VAL:A-10" structurePDB="7KHU" />
                            <MotifDetail num={2} sugar="FUC" rmsd="0.1 Å" residues="TRP: A-7, GLN: A-9, VAL:A-10" structurePDB="7KHU" />
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
