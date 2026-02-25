import { ChakraProvider } from "@chakra-ui/react"
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from "@tanstack/react-router"
import { router } from "./Router"

const queryClient = new QueryClient();

function App() {
    return (
        <ChakraProvider>
            <QueryClientProvider client={queryClient}>
                <RouterProvider router={router} />
            </QueryClientProvider>
        </ChakraProvider>
    )
}

export default App
