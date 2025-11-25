import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import SugarResults from "./pages/SugarResults";
import ResultDetail from "./pages/ResultDetail";

const rootRoute = createRootRoute({
    component: () => (
        <>
            <NavBar />
            <Outlet />
        </>
    ),
})

const sugarsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    component: Home,
})

export const sugarResultsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/sugars/$abrev",
    component: SugarResults,
})

const resultDetailRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/sugars/$abrev/$afId",
    component: ResultDetail,
})

const routeTree = rootRoute.addChildren([sugarsRoute, sugarResultsRoute, resultDetailRoute])

export const router = createRouter({ routeTree })
