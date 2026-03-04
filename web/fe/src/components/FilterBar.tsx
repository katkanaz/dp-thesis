import { QuestionOutlineIcon } from "@chakra-ui/icons"
import { Box, HStack, NumberDecrementStepper, NumberIncrementStepper, NumberInput, NumberInputField, NumberInputStepper, Select, Text, Tooltip, VStack } from "@chakra-ui/react"

function FilterBar() {
    return (
        <HStack>
            <VStack alignItems="letf">
                <HStack spacing="1">
                    <Text>
                        Sugar
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <Select>
                    <option value="" disabled selected>Select</option>
                    <option>FUC</option>
                    <option>GAL</option>
                    <option>GLC</option>
                </Select>
            </VStack>
            <VStack alignItems="letf">
                <HStack spacing="1">
                    <Text>
                        pLDDT
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <HStack>
                    <NumberInput width="24">
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                    <Box w="3" border="solid" borderWidth="0" borderBottomWidth="2px" borderColor="gray.700" />
                    <NumberInput width="24">
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                </HStack>
            </VStack>
            <VStack alignItems="letf">
                <HStack spacing="1">
                    <Text>
                        Organism
                    </Text>
                    <Tooltip label="Organism from which the protein originates from" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <Select>
                    <option value="" disabled selected>Select</option>
                    <option>Debaryomyces hansenii CBS767</option>
                    <option>Fonsecaea pedrosoi CBS 271.37</option>
                    <option>Madurella mycetomatis</option>
                </Select>
            </VStack>
            <VStack alignItems="letf">
                <HStack spacing="1">
                    <Text>
                        PDB Structure
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <Select>
                    <option value="" disabled selected>Select</option>
                    <option>7KHU</option>
                    <option>4D6D</option>
                    <option>1GWM</option>
                </Select>
            </VStack>
        </HStack>
    )
}

export default FilterBar
