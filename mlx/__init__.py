from .mlx import Mlx

# Create the singleton instance
_instance = Mlx()

# Map the class methods to the global functions display.py expects
init = _instance.mlx_init
new_window = _instance.mlx_new_window
new_image = _instance.mlx_new_image
get_data_addr = _instance.mlx_get_data_addr
put_image_to_window = _instance.mlx_put_image_to_window
key_hook = _instance.mlx_key_hook
loop_hook = _instance.mlx_loop_hook
loop = _instance.mlx_loop
string_put = _instance.mlx_string_put
destroy_image = _instance.mlx_destroy_image
hook = _instance.mlx_hook
