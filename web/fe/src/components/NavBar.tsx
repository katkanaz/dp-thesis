import { Box, Link as ChakraLink, HStack, Image, Text } from "@chakra-ui/react"
import { Link as TanstackRouterLink } from '@tanstack/react-router'
import logo from "../assets/logo.svg"

import { useQuery } from "@tanstack/react-query";
import { getLastModified, LastUpdated } from "../api/computed_structure";
import { docsRoute, homeRoute, resultsRoute, statsRoute } from "../Router";


function NavBar() {
    const { data: lastUpdated } = useQuery<LastUpdated, Error>({
        queryKey: ["lastModified"],
        queryFn: getLastModified
    });

    return (
        <Box background="white" shadow="sm" h="3.5em" display="flex" justifyContent="space-between" alignItems="center" px="6" top="0" position="sticky" zIndex="1000">
            <Box>
                <ChakraLink as={TanstackRouterLink} to={homeRoute.to} textDecoration="none" _hover={{ textDecoration: "none" }}>
                    <HStack spacing="1">
                        <Image src={logo} alt="Website Logo" boxSize="40px"/>
                        <Text fontWeight="bold" fontSize="lg">
                            Web Title
                        </Text>
                    </HStack>
                </ChakraLink>
            </Box>
            {lastUpdated &&
                <>
                    <Box ml="4" height="60%" borderLeft="1px" borderColor="gray.400"></Box>
                    <Box ml="4" color="gray.400">
                        Last updated {lastUpdated.date}
                    </Box>
                </>
            }
            <Box flexGrow="1"></Box>
            <HStack spacing="5">
                <ChakraLink as={TanstackRouterLink} to={homeRoute.to}>
                    Home
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to={resultsRoute.to}>
                    Results
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to={statsRoute.to}>
                    Statistics
                </ChakraLink>
                <ChakraLink as={TanstackRouterLink} to={docsRoute.to}>
                    Docs
                </ChakraLink>
            </HStack>
        </Box>
    )
}

export default NavBar
