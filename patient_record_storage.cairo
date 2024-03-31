%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.hash import hash2

@contract_interface
namespace IRecordStorage:
    func add_record(patient_id : felt, record_hash : felt):
    end
end

@storage_var
func records(patient_id : felt) -> (record_hash : felt):
end

func add_record{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(patient_id : felt, record_hash : felt):
    records.write(patient_id, record_hash)
    return ()
end

func get_record{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(patient_id : felt) -> (record_hash : felt):
    let (record_hash) = records.read(patient_id)
    return (record_hash)
end
