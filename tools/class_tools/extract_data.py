import numpy as np

def to_fixed_point(data,bit_width,frac_bits):

	out_data = 0
	max_val =(pow(2,bit_width-1) - 1) * pow(2, -frac_bits)
	min_val = - pow(2,bit_width-1) * pow (2, -frac_bits)

	if data > max_val:
		out_data = max_val
	elif data < min_val:
		out_data = min_val
	else: 
		out_data = data

	out_data = out_data * pow(2,frac_bits)
	out_data = int(round(out_data))	

	return out_data

def print_data(data_blobs,name,append,bit_width,frac):
##################################################
# TO NOTE: kernel is already transposed by caffe #
##################################################
        
        count = 0
        ch_out = data_blobs.shape[0]
        image_dim = 0
        val = 0

	image_list = data_blobs.tolist()
        #For bias and kernel the file should be overwritten only during the first layer
        if append:
                image_file = open(name,"a")
        else:
                image_file = open(name,"w")

	for c_o in range(ch_out):
                #To diferenciate between bias (shape only 1) and kernels and outputs
                if len(data_blobs.shape) == 4:
                        ch_in = data_blobs.shape[1]
                        image_dim = data_blobs.shape[2]

			for c_i in range(ch_in):
                                for h in range(image_dim):
                                        for w in range(image_dim):
                                                val = image_list[c_o][c_i][h][w]
                                                val = to_fixed_point(val,bit_width,frac)
                                                image_file.write(str(val) + ",")
                                                count = count + 1
                else:
                        val = image_list[c_o]
                        val = to_fixed_point(val,bit_width,frac)
                        image_file.write(str(val) + ",")

#	When kernel 1x1, fill with zeros to align
        if image_dim == 1:
                for i in range(9 - (count % 9)):
                        image_file.write("0,")

        image_file.close()


def print_weights(net,base_dir,wei_bit_width,wei_frac):
        bias_file = base_dir + "bias_all.txt"
        kernel_file = base_dir + "kernel_all.txt"
        
        append_file = False
        layer_names = list(net._layer_names)
        lay_count = 0

        for id,layer_name in enumerate(layer_names):
	
                layer  = net.layers[id]
                if (layer.type == "ConvolutionRistretto"):
                        frac_bits = wei_frac[lay_count]
                        kernels = net.params[layer_name][0].data[...]
                        biases = net.params[layer_name][1].data[...]

                        print_data(biases,bias_file,append_file,wei_bit_width,frac_bits)
                        print_data(kernels,kernel_file,append_file,wei_bit_width,frac_bits)

                        append_file = True
                        lay_count = lay_count + 1


def print_all_layers(net,base_dir,bit_width,lay_frac_out):
        layer_names = list(net._layer_names)
        lay_count = 0

        for id,layer_name in enumerate(layer_names):
                layer = net.layers[id]
                if (layer.type == "ConvolutionRistretto"):
                        frac_bits = lay_frac_out[lay_count]
                        blobs = net.blobs[layer_name].data[...]
                        name = base_dir + layer_name + ".txt"

                        print_data(blobs,name,False,bit_width,frac_bits)

                        lay_count = lay_count + 1
