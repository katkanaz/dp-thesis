import { Box, HStack, Input, InputGroup, InputLeftElement, InputRightElement, Kbd } from "@chakra-ui/react";
import MainContainer from "../components/MainContainer";
import NavBar from "../components/NavBar";
import { SearchIcon } from "@chakra-ui/icons";
import SugarCard, { type SugarInfo } from "../components/SugarCard";
import fucSpin from "../assets/fuc_spin.gif"

const sugarList: SugarInfo[] = [
    {
        name: "α-L-fucopyranose",
        abrev: "FUC",
        img: fucSpin,
    },
    {
        name: "β-L-fucopyranose",
        abrev: "FUL",
        img: fucSpin,
    },
    {
        name: "α-D-mannopyranose",
        abrev: "MAN",
        img: fucSpin,
    },
    {
        name: "β-D-galalctopyranose",
        abrev: "GAL",
        img: fucSpin,
    },
    {
        name: "α-D-glucopyranose",
        abrev: "GLC",
        img: fucSpin,
    },
    {
        name: "N-acetyl-α-D-neuraminic acid",
        abrev: "SIA",
        img: fucSpin,
    }
]

function Home() {
    return (
        <>
            <NavBar/>
            <MainContainer>
                <InputGroup mt="1rem"> {/* FIXME: instead of rem chakra consts */}
                    <InputLeftElement>
                        <SearchIcon color="gray.300" />
                    </InputLeftElement> 
                    <Input placeholder="Search" />
                    <InputRightElement color="gray.600" width="4.5rem" mr="0.8rem">
                        <Box display="flex" gap="1">
                            <Kbd>Ctrl</Kbd>
                            <Kbd>K</Kbd>
                        </Box>
                    </InputRightElement>
                </InputGroup>
                <HStack mt="8" wrap="wrap">
                    {sugarList.map(s => <SugarCard sugar={s} />)}
                </HStack>
            </MainContainer>
        </>
    )
}

export default Home
