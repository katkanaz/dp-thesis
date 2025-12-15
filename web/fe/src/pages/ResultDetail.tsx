import { Box, HStack, Link, Switch, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import type { ResultInfo } from "../components/SearchResultItem"
import { resultsList } from "./SugarResults"
import { resultDetailRoute } from "../Router";
import MolStarWrapper from "../components/MolStarWrapper";


function getSugarResult(_abrev: string, afId: string): ResultInfo | undefined {
    return resultsList.find(r => r.afid === afId) 
}


function ResultDetail() {
    const { abrev, afId } = resultDetailRoute.useParams()
    const result = getSugarResult(abrev, afId)
    if (result === undefined) {
        return (
            <MainContainer>
                <Box >Unknow AlphaFold ID</Box>
            </MainContainer>
        )
    }
    return (
        <MainContainer>
            <VStack width="100%" alignItems="flex-start" mt="3">
                <Box fontWeight="bold" fontSize="3xl">{result.title}</Box>
                <HStack width="100%" alignItems="flex-start">
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
                                            3
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">RMSD:</Td>
                                        <Td>
                                            0.1 Å
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Motif residues:</Td>
                                        <Td>
                                           TRP: A-7, GLN: A-9, VAL:A-10 
                                        </Td>
                                    </Tr>
                                    <Tr>
                                        <Td width="2" fontWeight="bold" px="0">Original structure PDB ID:</Td>
                                        <Td>
                                            <Link>
                                                7KHU
                                            </Link>
                                        </Td>
                                    </Tr>
                                </Tbody>
                            </Table>
                        </TableContainer>
                    </Box>
                    <VStack flexGrow="1">
                        <Box position="relative" width="100%" zIndex="10">
                            <MolStarWrapper />
                        </Box>
                        <Switch></Switch>
                    </VStack>
                </HStack>
            </VStack>
        </MainContainer>
    )
}

export default ResultDetail
