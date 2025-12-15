import { HStack, Image, Link, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react";

export type ResultInfo = {
    "title": string,
    "afid": string,
    "plddt_global": number,
    "organism": string,
    "uniprotid": string,
    "img": string,
};

interface SearchResultItemProps {
    result: ResultInfo
};

// NOTE: use uniprot ids and names, af id remains
function SearchResultItem({result}: SearchResultItemProps) {
    return (
        <HStack alignItems="flex-start" w="full">
            <Image src={result.img} inlineSize="80"/>
            <VStack alignItems="left">
                <Link fontSize="3xl" fontWeight="bold">
                    {result.title}
                </Link>
                <TableContainer>
                    <Table variant="striped" colorScheme="whiteAlpha" size="sm">
                        <Tbody>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">AlphaFold DB</Td>
                                <Td>
                                    <Link>
                                        {result.afid}
                                    </Link>
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">UniProtKB</Td>
                                <Td>
                                    <Link>
                                        {result.uniprotid}
                                    </Link>
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">pLDDT (global)</Td>
                                <Td>
                                    {result.plddt_global}
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
