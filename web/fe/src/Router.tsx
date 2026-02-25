import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import Results from "./pages/Results";
import ResultDetail from "./pages/ResultDetail";
import Docs from "./pages/Docs";

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
    path: "/results",
    component: Results,
})

export const resultDetailRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/results/$afId",
    component: ResultDetail,
})

const DocsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/docs",
    component: Docs,
})

const routeTree = rootRoute.addChildren([sugarsRoute, sugarResultsRoute, resultDetailRoute, DocsRoute])

export const router = createRouter({ routeTree })
