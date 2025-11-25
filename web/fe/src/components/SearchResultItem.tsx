import { HStack, Image, Link, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react";

export type ResultInfo = {
    "title": string,
    "id": string,
    "img": string,
};

interface SearchResultItemProps {
    result: ResultInfo
};

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
                                        {result.id}
                                    </Link>
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
