import { Box, Link as ChakraLink } from "@chakra-ui/react"
import { Link as TanstackRouterLink } from '@tanstack/react-router'

function NavBar() {
    return (
        <Box shadow="sm" h="3.5em" display="flex" justifyContent="space-between" alignItems="center" px="6">
            <Box>
                <ChakraLink as={TanstackRouterLink} to="/" textDecoration="none" _hover={{ textDecoration: "none" }}>
                    Logo/Title
                </ChakraLink>
            </Box>
            <ChakraLink href="/docs">
                Docs
            </ChakraLink>
        </Box>
    )
}

export default NavBar
