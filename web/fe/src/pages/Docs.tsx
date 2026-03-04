import MainContainer from "../components/MainContainer"
import { Box, Flex, Link, Text, VStack } from "@chakra-ui/react"

function Docs() {
    return (
        <MainContainer>
            <Flex>
                <Box mt="4" display={{ base: "none", md: "block" }} w="250px" h="fit-content" p={4} top="14" position="sticky">
                    <VStack align="start" spacing={3}>
                      <Link href="#web" fontWeight="bold">Web</Link>
                      <Link href="#web-overview">Overview</Link>
                      <Link href="#filters">Filters</Link>
                      <Link href="#workflow" fontWeight="bold">Workflow</Link>
                      <Link href="#workflow-overview">Overview</Link>
                      <Link href="#usage-instructions">Usage Instructions</Link>
                    </VStack>
                </Box>
                <Box flex="1" p={6}>
                    <VStack align="start" spacing={8}>
                        <Box id="web">
                            <Text fontSize="4xl" fontWeight="bold">Web</Text>
                            <Text></Text>
                        </Box>
                        <Box id="web-overview">
                            <Text fontSize="2xl" fontWeight="bold">Overview</Text>
                            <Text>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla ultrices blandit imperdiet. Aliquam eu viverra dolor, sit amet interdum dui. Curabitur luctus molestie sem, a ultrices velit molestie quis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec a suscipit ante, vitae tincidunt ex. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur eleifend velit eget orci ullamcorper gravida. Sed nec velit eget ex vestibulum placerat. Fusce quis sem vel lacus commodo sagittis. Nulla eget diam nec erat dignissim condimentum. Curabitur lobortis, sapien eget cursus tincidunt, massa libero iaculis augue, sed congue est quam et ex. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Donec consequat auctor erat non dapibus. Sed a ex tristique, molestie arcu sed, commodo erat. Etiam commodo ipsum quis sapien tincidunt pulvinar. Suspendisse scelerisque dictum ante, id facilisis nunc pretium a.
                            </Text>
                        </Box>
                        <Box id="filters">
                            <Text fontSize="2xl" fontWeight="bold">Filters</Text>
                            <Text>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla ultrices blandit imperdiet. Aliquam eu viverra dolor, sit amet interdum dui. Curabitur luctus molestie sem, a ultrices velit molestie quis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec a suscipit ante, vitae tincidunt ex. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur eleifend velit eget orci ullamcorper gravida. Sed nec velit eget ex vestibulum placerat. Fusce quis sem vel lacus commodo sagittis. Nulla eget diam nec erat dignissim condimentum. Curabitur lobortis, sapien eget cursus tincidunt, massa libero iaculis augue, sed congue est quam et ex. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Donec consequat auctor erat non dapibus. Sed a ex tristique, molestie arcu sed, commodo erat. Etiam commodo ipsum quis sapien tincidunt pulvinar. Suspendisse scelerisque dictum ante, id facilisis nunc pretium a.
                            </Text>
                        </Box>
                        <Box id="workflow">
                            <Text fontSize="4xl" fontWeight="bold">Workflow</Text>
                            <Text></Text>
                        </Box>
                        <Box id="workflow-overview">
                            <Text fontSize="2xl" fontWeight="bold">Overview</Text>
                            <Text>
                                Etiam sollicitudin, erat nec venenatis dignissim, metus mi iaculis nulla, convallis lobortis neque risus at arcu. Mauris imperdiet at ipsum ac ultricies. Morbi pulvinar orci ipsum, eget euismod lectus venenatis ac. Aliquam sit amet cursus quam. Mauris consectetur maximus suscipit. Aenean euismod vel sapien quis sodales. Mauris a nunc nec diam cursus dapibus nec nec neque. Pellentesque ex risus, posuere a metus at, ultrices viverra felis. Sed porttitor dui orci. Integer ligula eros, viverra quis purus sit amet, lobortis imperdiet neque. Proin at lorem nibh. Sed bibendum, nulla in aliquet dignissim, purus arcu imperdiet lorem, ac dapibus lorem metus at lacus. Morbi pulvinar porttitor elementum. Vivamus id dui at nunc molestie malesuada. Duis ut sapien sodales, venenatis ante non, placerat erat. Praesent interdum arcu id elementum commodo.
                            </Text>
                        </Box>
                        <Box id="usage-instructions">
                            <Text fontSize="2xl" fontWeight="bold">Usage Instructions</Text>
                            <Text>
                                Integer ullamcorper in neque porttitor laoreet. Integer metus tellus, lacinia id dolor lobortis, congue lacinia odio. Donec accumsan, sem sit amet sollicitudin lacinia, lorem mauris tincidunt sem, quis ultricies nibh dui sit amet eros. Aliquam mattis, velit non maximus malesuada, ipsum justo tempor mi, nec porttitor arcu purus eget nisi. Nam congue, urna eu vestibulum dictum, augue augue volutpat eros, id interdum felis diam tempus diam. Curabitur euismod velit neque, eu porttitor arcu efficitur quis. Maecenas tellus diam, sodales eget sollicitudin eget, ornare ut enim. Praesent sit amet ipsum id urna feugiat sollicitudin at sit amet eros. Mauris vel gravida lorem.
                            </Text>
                        </Box>
                    </VStack>
                </Box>
                </Flex>
        </MainContainer>
    )
}

// TODO: link to github?

export default Docs
