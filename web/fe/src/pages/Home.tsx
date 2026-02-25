import { Box, Input, InputGroup, InputLeftElement, InputRightElement, Kbd, SimpleGrid } from "@chakra-ui/react";
import { SearchIcon } from "@chakra-ui/icons";
import { useQuery } from "@tanstack/react-query";
import { getSugars, Sugar } from "../api/sugars";
import MainContainer from "../components/MainContainer";
import SugarCard from "../components/SugarCard";

//
// TODO: sugar names proper via regex - italics and smallcaps
// TODO: functional search bar, search bar match grid of sugars, sugar graphic pic, fix small caps and italic (not called this, not tag i) via CSS

function Home() {
    const { data: sugarList, isLoading, isError, error } = useQuery<Sugar[], Error>({
        queryKey: ["sugars"],
        queryFn: getSugars
    });

    if (isLoading) return <div>Loading sugars...</div>;
    if (isError) return <div>Error: {error.message}</div>;

    return (
        <MainContainer width="70%">
            <InputGroup mt="6">
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
            <Box display="flex" justifyContent="center"> 
                <SimpleGrid mt="8" minChildWidth={["60", "80"]} spacing="3" width="100%">
                    {sugarList?.map((s: Sugar) => <SugarCard key={s.name} sugar={s} />)}
                </SimpleGrid>
            </Box>
        </MainContainer>
    )
}


export default Home
