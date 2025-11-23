import { Card, CardBody, Image, Text } from "@chakra-ui/react";

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
        <Card maxW={["60", "80"]}>
            <CardBody display="flex" flexDir="column" alignItems="center">
                <Image src={sugar.img} />
                <Text>
                    {sugar.abrev}
                </Text>
                <Text>
                    {sugar.name}
                </Text>
            </CardBody>
        </Card> 
    )
}

export default SugarCard
