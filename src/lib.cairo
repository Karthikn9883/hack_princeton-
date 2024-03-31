%lang starknet

@contract_interface
namespace ICounter {
    func increase_counter(value : felt).
    func get_counter() -> (res : felt).
}

@storage_var
func counter() -> (res : felt) {
}

@external
func increase_counter(value : felt) {
    let (current_counter) = counter.read()
    counter.write(current_counter + value)
}

@view
func get_counter() -> (res : felt) {
    return (counter.read())
}
