import { QuestionOutlineIcon, SearchIcon } from "@chakra-ui/icons"
import { Box, Button, HStack, NumberInput, NumberInputField, RangeSlider, RangeSliderFilledTrack, RangeSliderThumb, RangeSliderTrack, Text, Tooltip, VStack } from "@chakra-ui/react"

import MultiSelect, { useMultiSelect } from "./MultiSelect";
import { FilterOptions, getFilterOptions } from "../api/computed_structure";
import { useQuery } from "@tanstack/react-query";


function FilterBar() {
    const { data, isLoading, isError } = useQuery<FilterOptions, Error>({
        queryKey: ["options"],
        queryFn: getFilterOptions
    });
    const sugarMultiSelect = useMultiSelect(data?.sugars, { isLoading, isError })
    const organismMultiSelect = useMultiSelect(data?.organisms, { isLoading, isError })
    const pdbStructMultiSelect = useMultiSelect(data?.pdb_structures, { isLoading, isError })

    return (
        <HStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1" w="full">
                    <Text>
                        Sugar
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                    {sugarMultiSelect.props.selected.length > 0 &&
                        <Button variant="ghost" size="xs" ml="auto" fontStyle="italic" color="gray.400" onClick={() => sugarMultiSelect.clearSelected()}>
                            clear
                        </Button>
                    }
                </HStack>
                <MultiSelect {...sugarMultiSelect.props} width="6rem" placeholder="e.g. GLC"/>
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
                <VStack>
                    <RangeSlider aria-label={["min", "max"]} defaultValue={[10, 30]}>
                        <RangeSliderTrack>
                            <RangeSliderFilledTrack />
                        </RangeSliderTrack>
                        <RangeSliderThumb index={0} />
                        <RangeSliderThumb index={1} />
                    </RangeSlider>
                    <HStack>
                        <NumberInput width="3rem" size="xs">
                          <NumberInputField borderRadius="md" />
                        </NumberInput>
                        <Box w="3" border="solid" borderWidth="0" borderBottomWidth="2px" borderColor="gray.700" />
                        <NumberInput width="3rem" size="xs">
                          <NumberInputField borderRadius="md" />
                        </NumberInput>
                    </HStack>
                </VStack>
            </VStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1" w="full">
                    <Text>
                        Organism
                    </Text>
                    <Tooltip label="Organism from which the protein originates from" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                    {organismMultiSelect.props.selected.length > 0 &&
                        <Button variant="ghost" size="xs" ml="auto" fontStyle="italic" color="gray.400" onClick={() => organismMultiSelect.clearSelected()}>
                            clear
                        </Button>
                    }
                </HStack>
                <MultiSelect {...organismMultiSelect.props} width="16rem" placeholder="e.g. Madurella mycetomatis"/>
            </VStack>
            <VStack alignItems="flex-start">
                <HStack spacing="1" w="full">
                    <Text>
                        PDB Structure
                    </Text>
                    <Tooltip label="" fontSize="sm">
                        <QuestionOutlineIcon boxSize="3.5" />
                    </Tooltip>
                    {pdbStructMultiSelect.props.selected.length > 0 &&
                        <Button variant="ghost" size="xs" ml="auto" fontStyle="italic" color="gray.400" onClick={() => pdbStructMultiSelect.clearSelected()}>
                            clear
                        </Button>
                    }
                </HStack>
                <MultiSelect {...pdbStructMultiSelect.props} width="7rem" placeholder="e.g. 7KHU"/>
            </VStack>
            <Button aria-label="Filter results" leftIcon={<SearchIcon aria-label="Search icon" />} ml="auto" color="gray.600">
                Filter
            </Button>
        </HStack>
    )
}

export default FilterBar
