import { Box, Link, Table, TableContainer, Tbody, Td, Tr, VStack } from "@chakra-ui/react"

type MotifDetailProps = {
    num: number
    sugar: string
    rmsd: string
    residues: string
    structurePDB: string
}

function MotifDetail({num, sugar, rmsd, residues, structurePDB}: MotifDetailProps) {
    return (
        <VStack alignItems="flex-start" border="1px" borderColor="rgb(206, 201, 186)">
            <Box background="orange.100" w="full" px="3" py="2">
                Motif {num}
            </Box>
            <Box px="3" pb="2">
                <TableContainer>
                    <Table variant="striped" colorScheme="whiteAlpha" size="sm">
                        <Tbody>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">Sugar:</Td>
                                <Td>
                                    {sugar}
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">RMSD:</Td>
                                <Td>
                                    {rmsd}
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">Motif residues:</Td>
                                <Td>
                                   {residues}
                                </Td>
                            </Tr>
                            <Tr>
                                <Td width="2" fontWeight="bold" px="0">Original structure PDB ID:</Td>
                                <Td>
                                    <Link>
                                        {structurePDB}
                                    </Link>
                                </Td>
                            </Tr>
                        </Tbody>
                    </Table>
                </TableContainer>
            </Box>
        </VStack>
    )
}

export default MotifDetail
