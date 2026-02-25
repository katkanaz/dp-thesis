import { Box, Link as ChakraLink, HStack } from "@chakra-ui/react"
import { Link as TanstackRouterLink } from '@tanstack/react-router'

function NavBar() {
    return (
        <Box shadow="sm" h="3.5em" display="flex" justifyContent="space-between" alignItems="center" px="6">
            <Box>
                <ChakraLink as={TanstackRouterLink} to="/" textDecoration="none" _hover={{ textDecoration: "none" }}>
                    Logo/Title
                </ChakraLink>
            </Box>
            <Box ml="4" height="60%" borderLeft="1px" borderColor="gray.400"></Box>
            <Box ml="4" color="gray.400">
                last updated 2025-12-12
            </Box>
            <Box flexGrow="1"></Box>
            <HStack spacing="2">
                <ChakraLink as={TanstackRouterLink} to="/">
                    Home
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to="/docs">
                    Docs
                </ChakraLink>
            </HStack>
        </Box>
    )
}

export default NavBar
