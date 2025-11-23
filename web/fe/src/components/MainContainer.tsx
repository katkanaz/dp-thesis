import { Box } from "@chakra-ui/react";
import type { ReactNode } from "react";

interface MainContainerProps {
    children?: ReactNode | ReactNode[]
};

function MainContainer(props: MainContainerProps) {
    return (
        <Box as="main" px="6">
            {props.children}
        </Box>
    )
}

export default MainContainer
