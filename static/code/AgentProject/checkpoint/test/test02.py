from masfactory.checkpoint.storage import FileCheckpointStorage
from pathlib import Path 

storage=FileCheckpointStorage(str(Path(__file__).parent))

checkpoint_state={
    "hello":"world",
    "count":2
}

checkpoint_path=storage.save(checkpoint_state)
print(storage.load(checkpoint_path))

print(__file__)
print(type(__file__))