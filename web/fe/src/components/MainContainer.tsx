import { Box } from "@chakra-ui/react";
import type { ReactNode } from "react";

interface MainContainerProps {
    width?: string|string[]|object
    children?: ReactNode | ReactNode[]
};

function MainContainer({children, width = {base: "100%", lg: "60%"}}: MainContainerProps) {
    return (
        <Box as="main" display="flex" justifyContent="center">
            <Box width={width}>
                {children}
            </Box>
        </Box>
    )
}

export default MainContainer
