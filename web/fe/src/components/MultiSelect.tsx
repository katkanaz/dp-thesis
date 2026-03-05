import { Combobox } from "@base-ui/react/combobox"
import { SmallCloseIcon } from "@chakra-ui/icons"
import { Box, IconButton, Input, List, ListItem } from "@chakra-ui/react"
import { useRef, useState } from "react"

export type MultiSelectOption = {
    id: number,
    value: string
}

interface MultiSelectProps {
    options: MultiSelectOption[]
    query: string 
    setQuery: (query: string) => void
    selected: MultiSelectOption[]
    setSelected: (selected: MultiSelectOption[]) => void
    width?: string
}

export function useMultiSelect() {
    const [ query, setQuery ] = useState("")
    const [ selected, setSelected ] = useState<MultiSelectOption[]>([])
    const multiSelectReturn = { query, setQuery, selected, setSelected }
    return multiSelectReturn
}

function MultiSelect({ options, query, setQuery, selected, setSelected, width }: MultiSelectProps) {
    const filtered = options.filter((item) =>
        item.value.toLowerCase().includes(query.toLowerCase())
    )
    const containerRef = useRef<HTMLDivElement | null>(null);

    return (
        <Combobox.Root
            value={selected}
            multiple
            onValueChange={setSelected}
        >
                <Box display="flex" flexDir="column" gap="0.25rem" maxW="20rem">
                    {/* <label htmlFor="test-combo">Filter frameworks...</label> */}
                    <Combobox.Chips ref={containerRef} render={(props) => (
                        <Box {...props} display="flex" flexWrap="wrap" alignItems="center" gap="0.125rem" border="1px solid" borderColor="gray.200" borderRadius="md" />
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
                                        id="test-combo"
                                        render={(props) => (
                                            <Input
                                                minW="3rem"
                                                flex="1"
                                                width={width ?? "5rem"}
                                                border="none"
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
                            {filtered.map((item) => (
                                <Combobox.Item
                                    key={item.id}
                                    value={item}
                                    render={(props, state) => (
                                        <ListItem //TODO: render check icon if state.selected true - javascript {} above item value
                                            {...props}
                                            px={3}
                                            py={2}
                                            cursor="pointer"
                                            bg={
                                                state.highlighted
                                                    ? "gray.100"
                                                    : "transparent"
                                            }
                                            fontWeight={
                                                state.selected ? "bold" : "normal"
                                            }
                                        >
                                            {item.value}
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
