import { HStack, Image, Link as ChakraLink, Table, TableContainer, Tbody, Td, Tr, VStack, Box } from "@chakra-ui/react";
import { Link as TanstackRouterLink } from '@tanstack/react-router'
import { ComputedStructure } from "../api/computed_structure";
import placeholder from "../assets/logo.svg"


//TODO: img jinak - request na api/img, klice nemusi byt ve stringu, musi odpovidat json klicum, definovat v api aby kopirovalo json cely - ComputedStructure type


interface SearchResultItemProps {
    result: ComputedStructure
};


function SearchResultItem({result}: SearchResultItemProps) {
    return (
        <HStack align="flex-start" w="full" spacing={4}>
            <Box boxSize="250px" flexShrink={0}>
                <ChakraLink  as={TanstackRouterLink} to={result.afdb_id}>
                    <Image src={placeholder} boxSize="250px" objectFit="cover" borderRadius="md"/>
                </ChakraLink>
            </Box>
            <VStack align="left-start" spacing={3} flex="1" minW={0}>
                <ChakraLink as={TanstackRouterLink} to={result.afdb_id} fontSize="2xl" fontWeight="bold" w="full">
                    {result.title}
                </ChakraLink>
                <TableContainer w="full" m={0}>
                    <Table variant="striped" colorScheme="whiteAlpha" size="sm">
                        <Tbody>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">AlphaFold DB</Td>
                                <Td>
                                    <ChakraLink href={`https://alphafold.ebi.ac.uk/entry/${result.afdb_id.split("-")[1]}`}>
                                        {result.afdb_id}
                                    </ChakraLink>
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">UniProtKB</Td>
                                <Td>
                                    <ChakraLink href={`https://www.uniprot.org/uniprotkb/${result.afdb_id.split("-")[1]}`}>
                                        {`${result.afdb_id.split("-")[1]}`}
                                    </ChakraLink>
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">pLDDT (global)</Td>
                                <Td>
                                    {result.plddt}
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">Organism</Td>
                                <Td>
                                    {result.organism}
                                </Td>
                            </Tr>
                        </Tbody>
                    </Table>
                </TableContainer>
            </VStack>
        </HStack>
    )
}

export default SearchResultItem
