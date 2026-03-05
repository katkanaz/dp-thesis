import { QuestionOutlineIcon } from "@chakra-ui/icons"
import { Box, HStack, NumberDecrementStepper, NumberIncrementStepper, NumberInput, NumberInputField, NumberInputStepper, Text, Tooltip, VStack } from "@chakra-ui/react"

import MultiSelect, { MultiSelectOption, useMultiSelect } from "./MultiSelect";

const sugarOptions: MultiSelectOption[] = [
    { id: 1, value: "FUC" },
    { id: 2, value: "FUL" },
    { id: 3, value: "GLC" },
    { id: 4, value: "GAL" },
    { id: 5, value: "SIA" }
]

const orgOptions: MultiSelectOption[] = [
    { id: 1, value: "Lactobacillus" },
    { id: 2, value: "Escherichia" },
    { id: 3, value: "Debaryomyces hansenii CBS767" },
    { id: 4, value: "Madurella mycetomatis" },
    { id: 5, value: "Neisseria gonorrhoeae" }
]

const pdbOptions: MultiSelectOption[] = [
    { id: 1, value: "7KHU" },
    { id: 2, value: "4D6D" },
    { id: 3, value: "1AGW" },
    { id: 4, value: "7C7B" },
    { id: 5, value: "1AMG" }
]

function FilterBar() {
    const sugarMultiSelect = useMultiSelect()
    const organismMultiSelect = useMultiSelect()
    const pdbStructMultiSelect = useMultiSelect()
    return (
        <HStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1">
                    <Text>
                        Sugar
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <MultiSelect options={sugarOptions} {...sugarMultiSelect}/>
            </VStack>
            <VStack alignItems="flex-start">
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
                    <NumberInput width="24" size="xs">
                      <NumberInputField />
                      {/* <NumberInputStepper> */}
                      {/*   <NumberIncrementStepper /> */}
                      {/*   <NumberDecrementStepper /> */}
                      {/* </NumberInputStepper> */}
                    </NumberInput>
                </HStack>
            </VStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1">
                    <Text>
                        Organism
                    </Text>
                    <Tooltip label="Organism from which the protein originates from" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <MultiSelect options={orgOptions} {...organismMultiSelect} width="16rem"/>
            </VStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1">
                    <Text>
                        PDB Structure
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                </HStack>
                <MultiSelect options={pdbOptions} {...pdbStructMultiSelect} width="6rem"/>
            </VStack>
        </HStack>
    )
}

export default FilterBar
