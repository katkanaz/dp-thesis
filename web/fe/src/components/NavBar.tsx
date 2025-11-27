import { Box, Link } from "@chakra-ui/react"

function NavBar() {
    return (
        <Box shadow="sm" h="3.5em" display="flex" justifyContent="space-between" alignItems="center" px="6">
            <Box>
                Logo/Title
            </Box>
            <Link href="/docs">
                Docs
            </Link>
        </Box>
    )
}

export default NavBar
