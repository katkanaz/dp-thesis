import { Combobox } from "@base-ui/react/combobox"
import { CheckIcon, SmallCloseIcon } from "@chakra-ui/icons"
import { Box, HStack, IconButton, Input, List, ListItem } from "@chakra-ui/react"
import { useRef, useState } from "react"

export type MultiSelectOption = {
    id: number,
    value: string
}

type OptionInfo = {
    isLoading: boolean,
    isError: boolean,
}

interface MultiSelectProps {
    options: MultiSelectOption[]
    optionInfo: OptionInfo
    query: string 
    setQuery: (query: string) => void
    selected: MultiSelectOption[]
    setSelected: (selected: MultiSelectOption[]) => void
    width?: string
    placeholder: string
}

export function useMultiSelect(options: MultiSelectOption[] | undefined, optionInfo: OptionInfo) {
    const [ query, setQuery ] = useState("")
    const [ selected, setSelected ] = useState<MultiSelectOption[]>([])
    const clearSelected = () => {
        setSelected([])
    }
    const multiSelectReturn = { props: { query, setQuery, selected, setSelected, options: options ?? [], optionInfo}, clearSelected }
    return multiSelectReturn
}

function MultiSelect({ options, optionInfo, query, setQuery, selected, setSelected, width, placeholder }: MultiSelectProps) {
    const filtered = options?.filter((item) =>
        item.value.toLowerCase().includes(query.toLowerCase())
    )
    const containerRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement|null>(null);

    return (
        <Combobox.Root
            value={selected}
            multiple
            onValueChange={setSelected}

        >
            <Box display="flex" flexDir="column" gap="0.25rem" maxW="20rem">
                <Combobox.Chips ref={containerRef} render={(props) => (
                    <Box 
                        {...props}
                        display="flex"
                        flexWrap="wrap"
                        alignItems="center"
                        gap="0.125rem"
                        border="1px solid"
                        borderColor="gray.200"
                        borderRadius="md"
                        cursor="text"
                        onClick={() => inputRef.current?.focus()}
                        _focusWithin={{ borderColor: "blue.500", boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)" }}

                    />
                )}>
                    <Combobox.Value>
                        {(value: MultiSelectOption[]) => (
                            <>
                                {value.map((option) => (
                                    <Combobox.Chip
                                        key={option.id}
                                        aria-label={option.value}
                                        render={(props) => (
                                            <Box {...props} display="flex" alignItems="center" border="1px solid" borderColor="gray.200" borderRadius="md" p="1">
                                                {option.value}
                                                <Combobox.ChipRemove aria-label="Remove" render={(props) => (
                                                    <IconButton {...props as any} icon={<SmallCloseIcon />} size="xs" variant="ghost"/>
                                                )} />
                                            </Box>
                                        )}
                                    >
                                    </Combobox.Chip>
                                ))}
                                <Combobox.Input
                                    placeholder={value.length > 0 ? "" : placeholder}
                                    ref={inputRef}
                                    render={(props) => (
                                        <Input
                                            minW="3rem"
                                            flex="1"
                                            width={width ?? "5rem"}
                                            border="none"
                                            // _focusVisible={{ borderColor: "blue.500", boxShadow: "0 0 0 2px var(--chakra-colors-blue-500)" }}
                                            _focusVisible={{outline: "none"}}
                                            _selected={{outline: "none"}}
                                            {...props}
                                            onChange={(e) => {
                                                props.onChange?.(e)
                                                setQuery(e.target.value)
                                            }}
                                        />
                                    )}
                                />
                            </>
                        )}
                    </Combobox.Value>
                </Combobox.Chips>
            </Box>
                <Combobox.Portal>
                    <Combobox.Positioner anchor={containerRef}>
                        <Combobox.Popup
                            render={(props) => (
                                <List
                                    {...props}
                                    mt={2}
                                    borderWidth="1px"
                                    borderRadius="md"
                                    maxH="200px"
                                    width="var(--anchor-width)"
                                    overflowY="auto"
                                    bg="white"
                                />
                            )}
                        >
                            {/* {optionInfo.isLoading && spinner} */}
                            {/* {optionInfo.isError && message} */}
                            {filtered.map((item) => (
                                <Combobox.Item
                                    key={item.id}
                                    value={item}
                                    render={(props, state) => (
                                        <ListItem
                                            {...props}
                                            px={3}
                                            py={2}
                                            cursor="pointer"
                                            bg={
                                                state.highlighted
                                                    ? "gray.100"
                                                    : "transparent"
                                            }
                                        >
                                            <HStack>
                                                <Box w="3" h="3" display="flex" alignItems="center" justifyContent="center">
                                                    {state.selected &&
                                                        <CheckIcon boxSize="3"/>
                                                    }
                                                </Box>
                                                <Box>
                                                    {item.value}
                                                </Box>
                                            </HStack>
                                        </ListItem>
                                    )}
                                />
                            ))}
                        </Combobox.Popup>
                    </Combobox.Positioner>
                </Combobox.Portal>

        </Combobox.Root>
    )
}

export default MultiSelect
