import { Box, HStack, Input, InputGroup, InputLeftElement, InputRightElement, Kbd } from "@chakra-ui/react";
import MainContainer from "../components/MainContainer";
import { SearchIcon } from "@chakra-ui/icons";
import SugarCard, { type SugarInfo } from "../components/SugarCard";

import fucSpin from "../assets/fuc_spin_2.gif"
import fulSpin from "../assets/ful_spin_2.gif"
import manSpin from "../assets/man_spin_2.gif"
import galSpin from "../assets/gal_spin_2.gif"
import glcSpin from "../assets/glc_spin_2.gif"
import siaSpin from "../assets/sia_spin_2.gif"

export const sugarList: SugarInfo[] = [
    {
        name: "α-L-fucopyranose",
        abrev: "FUC",
        img: fucSpin,
    },
    {
        name: "β-L-fucopyranose",
        abrev: "FUL",
        img: fulSpin,
    },
    {
        name: "α-D-mannopyranose",
        abrev: "MAN",
        img: manSpin,
    },
    {
        name: "β-D-galalctopyranose",
        abrev: "GAL",
        img: galSpin,
    },
    {
        name: "α-D-glucopyranose",
        abrev: "GLC",
        img: glcSpin,
    },
    {
        name: "N-acetyl-α-D-neuraminic acid",
        abrev: "SIA",
        img: siaSpin,
    }
]
// TODO: functional search bar, search bar match grid of sugars, sugar graphic pic, fix small caps and italic (not called this, not tag i) via CSS

function Home() {
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
                <HStack mt="8" wrap="wrap">
                    {sugarList.map(s => <SugarCard sugar={s} />)} {/* TODO: Change to grid, card not capped width but width 100% within grid */}
                </HStack>
            </Box>
        </MainContainer>
    )
}

export default Home
