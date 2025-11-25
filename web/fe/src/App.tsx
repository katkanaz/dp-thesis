import { ChakraProvider } from "@chakra-ui/react"
import { RouterProvider } from "@tanstack/react-router"
import { router } from "./Router"

function App() {
    return (
        <ChakraProvider>
            <RouterProvider router={router} />
        </ChakraProvider>
    )
}

export default App
