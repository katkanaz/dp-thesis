import { SearchIcon } from "@chakra-ui/icons"
import { InputGroup, InputLeftElement, Input, InputRightElement, Box, Kbd, VStack, Text } from "@chakra-ui/react"
import MainContainer from "../components/MainContainer"
import SearchResultItem, { type ResultInfo } from "../components/SearchResultItem"

import fucosyltransferase from "../assets/fucosyltransferase.jpeg"
import unchar from "../assets/domain-containing.jpeg"
import lectin from "../assets/lectin.jpeg"
import { sugarList } from "./Home"
import { sugarResultsRoute } from "../Router"

const resultsList: ResultInfo[] = [
    {
        "title": "Alpha-(1,3)-fucosyltransferase",
        "afid": "AF-O25142-F1",
        "uniprotid": "O25142",
        "img": fucosyltransferase,
    },
    {
        "title": "Thioredoxin domain-containing protein",
        "afid": "AF-A0A0K0EH67-F1",
        "uniprotid": "A0A0K0EH67",
        "img": unchar,
    },
    {
        "title": "Lectin",
        "afid": "AF-P86993-F1",
        "uniprotid": "P86993",
        "img": lectin,
    },
]
// NOTE: "Computed model of" is added by RCSB, unchar. protein has different name in AFDB, AFDB ID: AF-O25142-F1 but RCSB AF_AFO25142F1

function SugarResults() {
    const { abrev } = sugarResultsRoute.useParams()
    const sugarInfo = sugarList.find(s => s.abrev === abrev)
    if (sugarInfo === undefined) {
        return (
            <Box>
                Sugar {abrev} not found!
            </Box>
        )
    }
    return (
        <MainContainer width="70%">
            <Text fontWeight="bold" mt="6" fontSize="4xl">
                Search Results for {sugarInfo?.name} ({sugarInfo?.abrev})
            </Text>
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
                {resultsList.map(r => <SearchResultItem result={r} />)}
            </VStack>
        </MainContainer>
    )
}

export default SugarResults
