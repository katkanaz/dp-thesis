import { Box, Link as ChakraLink, HStack, Image, Text } from "@chakra-ui/react"
import { Link as TanstackRouterLink } from '@tanstack/react-router'
import logo from "../assets/logo.svg" // TODO: wheren to store logo?


function NavBar() {
    return (
        <Box shadow="sm" h="3.5em" display="flex" justifyContent="space-between" alignItems="center" px="6">
            <Box>
                <ChakraLink as={TanstackRouterLink} to="/" textDecoration="none" _hover={{ textDecoration: "none" }}>
                    <HStack spacing="1">
                        <Image src={logo} alt="Website Logo" boxSize="40px"/>
                        <Text fontWeight="bold" fontSize="lg">
                            Web Title
                        </Text>
                    </HStack>
                </ChakraLink>
            </Box>
            <Box ml="4" height="60%" borderLeft="1px" borderColor="gray.400"></Box>
            <Box ml="4" color="gray.400">
                Last updated 2025-12-12
            </Box>
            <Box flexGrow="1"></Box>
            <HStack spacing="5">
                <ChakraLink as={TanstackRouterLink} to="/">
                    Home
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to="/">
                    Statistics
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to="/docs">
                    Docs
                </ChakraLink>
            </HStack>
        </Box>
    )
}

export default NavBar
