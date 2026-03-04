import { Link as TanstackRouterLink } from '@tanstack/react-router'
import { Card, CardBody, Image, Link as ChakraLink, Text } from "@chakra-ui/react";

export type SugarInfo = {
    name: string
    abrev: string
    img: string 
};

interface SugarCardProps {
    sugar: SugarInfo
};

function SugarCard({sugar}: SugarCardProps) {
    return (
        <ChakraLink as={TanstackRouterLink} to="/results" textDecoration="none" _hover={{ textDecoration: "none", shadow: "lg" }}>
            <Card>
                <CardBody display="flex" flexDir="column" alignItems="center">
                    <Image src={`api/img/${sugar.img}`} />
                    <Text>
                        {sugar.abrev}
                    </Text>
                    <Text>
                        {sugar.name}
                    </Text>
                </CardBody>
            </Card> 
        </ChakraLink>
    )
}

export default SugarCard
