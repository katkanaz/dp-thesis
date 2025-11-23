import { Box } from "@chakra-ui/react";
import type { ReactNode } from "react";

interface MainContainerProps {
    width?: string
    children?: ReactNode | ReactNode[]
};

function MainContainer(props: MainContainerProps) {
    return (
        <Box as="main" display="flex" justifyContent="center">
            <Box width={props.width}>
                {props.children}
            </Box>
        </Box>
    )
}

export default MainContainer
