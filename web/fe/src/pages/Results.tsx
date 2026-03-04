import { SearchIcon } from "@chakra-ui/icons"
import { InputGroup, InputLeftElement, Input, InputRightElement, Box, Kbd, VStack, Center, Spinner, Text, AlertIcon, Alert, AlertTitle, AlertDescription } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import SearchResultItem from "../components/SearchResultItem"

import { getResults, ComputedStructure } from "../api/computed_structure";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import FilterBar from "../components/FilterBar";

// NOTE: "Computed model of" is added by RCSB, unchar. protein has different name in AFDB, AFDB ID: AF-O25142-F1 but RCSB AF_AFO25142F1


function Results() {
    const [query, setQuery] = useState("")
      const inputRef = useRef<HTMLInputElement>(null)

      useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // FIXME: also meta key, chakra works different?
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault()
            inputRef.current?.focus()
          }
        }

        window.addEventListener("keydown", handleKeyDown)
        return () => window.removeEventListener("keydown", handleKeyDown)
      }, [])


    const { data: resultsList, isLoading, isError } = useQuery<ComputedStructure[], Error>({
        queryKey: ["results"],
        queryFn: getResults
    });

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


    return (
        <MainContainer>
            <InputGroup mt="6" mb="4">
                <InputLeftElement>
                    <SearchIcon color="gray.300" />
                </InputLeftElement> 
                <Input ref={inputRef} placeholder="Search" value={query} onChange={(e) => setQuery(e.target.value)} />
                <InputRightElement color="gray.600" width="20" mr="2">
                    <Box display="flex" gap="1">
                        <Kbd>Ctrl</Kbd>
                        <Kbd>K</Kbd>
                    </Box>
                </InputRightElement>
            </InputGroup>
            <FilterBar />
            <VStack mt="6" divider={<Box borderBottom="solid" borderBottomColor="lightgrey" borderBottomWidth="thin" boxSize="full" w="full"></Box>}>
                {resultsList?.length === 0 &&
                    <Box>
                        No results found
                    </Box>
                }
                {resultsList?.map(r => <SearchResultItem result={r} />)}
            </VStack>
        </MainContainer>
    )
}

// TODO: how many results displayed overall, choose how many on page + go to next page

export default Results
