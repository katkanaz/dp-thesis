import { SearchIcon } from "@chakra-ui/icons"
import { InputGroup, InputLeftElement, Input, InputRightElement, Box, Kbd, VStack } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import SearchResultItem from "../components/SearchResultItem"

import { getResults, ComputedStructure } from "../api/computed_structure";
import { useQuery } from "@tanstack/react-query";

// NOTE: "Computed model of" is added by RCSB, unchar. protein has different name in AFDB, AFDB ID: AF-O25142-F1 but RCSB AF_AFO25142F1


function Results() {
    const { data: resultsList, isLoading, isError, error } = useQuery<ComputedStructure[], Error>({
        queryKey: ["results"],
        queryFn: getResults
    });

    if (isLoading) return <div>Loading results...</div>;
    if (isError) return <div>Error: {error.message}</div>;

    // const { abrev } = sugarResultsRoute.useParams()
    // const sugarInfo = sugarList?.find((s: Sugar) => s.abrev === abrev)
    // if (sugarInfo === undefined) {
    //     return (
    //         <Box>
    //             Sugar {abrev} not found!
    //         </Box>
    //     )
    // }

    // const { data, isPending, error } = useQuery({
    //     queryKey: ['results'],
    //     queryFn: () => fetch('/api/results').then(r => r.json()),
    // })



    return (
        <MainContainer>
            {/* <Text fontWeight="bold" mt="6" fontSize="4xl"> */}
            {/*     Search Results for {sugarInfo?.name} ({sugarInfo?.abrev}) */}
            {/* </Text> */}
            <InputGroup mt="6" width="40%">
                <InputLeftElement>
                    <SearchIcon color="gray.300" />
                </InputLeftElement> 
                <Input placeholder="Search" />
                <InputRightElement color="gray.600" width="20" mr="2">
                    <Box display="flex" gap="1">
                        <Kbd>Ctrl</Kbd>
                        <Kbd>K</Kbd>
                    </Box>
                </InputRightElement>
            </InputGroup>
            <VStack mt="6" divider={<Box borderBottom="solid" borderBottomColor="lightgrey" borderBottomWidth="thin" boxSize="full" w="full"></Box>}>
                {resultsList?.map(r => <SearchResultItem result={r} />)}
            </VStack>
        </MainContainer>
    )
}

// TODO: how many results displayed overall, choose how many on page + go to next page

export default Results
