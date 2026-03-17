import { Alert, AlertDescription, AlertIcon, AlertTitle, Box, Center, HStack, Link, Spinner, Table, TableContainer, Tbody, Td, Text, Tr, VStack } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import { getCompStruct, ComputedStructure, mergeRisudeInfo } from "../api/computed_structure"
import { resultDetailRoute } from "../Router";
import MotifDetail from "../components/MotifDetail";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { MolStarWrapper } from "../components/MolStarWrapper";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { Download, ParseCif } from "molstar/lib/mol-plugin-state/transforms/data";
import { ModelFromTrajectory, StructureComponent, StructureFromModel, TrajectoryFromMmCif } from "molstar/lib/mol-plugin-state/transforms/model";
import { StructureRepresentation3D } from "molstar/lib/mol-plugin-state/transforms/representation";


function ResultDetail() {
    const { afId } = resultDetailRoute.useParams();

    const { data: compStruct, isLoading, isError } = useQuery<ComputedStructure, Error>({
        queryKey: ["comp-struct"],
        queryFn: () => getCompStruct(afId)
    });

    const [ molStar, setMolStar ] = useState<PluginUIContext|undefined>(undefined);

    useEffect(() => {
        if (!compStruct || !molStar) return
        molStar
            .build()
            .toRoot()
            .apply(Download, {url: `https://models.rcsb.org/${compStruct.pdb_id}.bcif`, isBinary: true})
            .apply(ParseCif)
            .apply(TrajectoryFromMmCif)
            .apply(ModelFromTrajectory)
            .apply(StructureFromModel)
            .apply(StructureComponent, {type: {name: "static", params: "polymer"}})
            .apply(StructureRepresentation3D, {
                type: {name: "cartoon", params: {alpha: 1, ignoreLight: false}},
                colorTheme: {name: "plddt-confidence", params: {}}
            }).commit()
    }, [compStruct, molStar]);

    // color_from_source
    // palette - DiscretePalete
    // examples.py, jupiternotebook setup

    if (isLoading) {
        return (
            <Center minH="60vh">
                <VStack spacing={4}>
                    <Spinner size="xl" thickness="4px" />
                    <Text fontSize="lg" color="gray.500">
                        Loading results...
                    </Text>
                </VStack>
            </Center>
        )
    }
    if (isError) {
        return (
            <Center minH="60vh">
                <VStack spacing={4}>
                    <Alert
                        status="error"
                        variant="subtle"
                        flexDirection="column"
                        alignItems="center"
                        justifyContent="center"
                        textAlign="center"
                        borderRadius="lg"
                        maxW="md"
                    >
                        <AlertIcon boxSize="40px" mr={0} />
                        <AlertTitle mt={4} mb={1} fontSize="lg">
                            Something went wrong
                        </AlertTitle>
                        <AlertDescription>
                            We couldn’t load your results. Please try again.
                        </AlertDescription>
                    </Alert>
                </VStack>
            </Center>
        )
    }

    if (compStruct === undefined) {
        return (
            <MainContainer>
                <Box >Unknow AlphaFold ID</Box>
            </MainContainer>
        )
    }

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
                        <VStack mt="3">
                            {compStruct.motifs.map((m, i) => <MotifDetail num={i+1} sugar={m.sugar} rmsd={m.score} residues={mergeRisudeInfo(m.residue_types, m.residue_ids)} structurePDB={m.original_struct} />)}
                        </VStack>
                    </Box>
                    <VStack flexGrow="1">
                        <Box position="relative" width="100%" zIndex="10">
                            <MolStarWrapper setMolStar={setMolStar} />
                        </Box>
                    </VStack>
                </HStack>
            </VStack>
        </MainContainer>
    )
}

export default ResultDetail
