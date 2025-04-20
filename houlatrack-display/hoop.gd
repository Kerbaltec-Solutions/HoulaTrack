# server_node.gd
class_name ServerNode
extends Node3D

var server = UDPServer.new()
var peers = []

func _ready():
	server.listen(5501)

func _process(delta):
	server.poll() # Important!
	if server.is_connection_available():
		var peer = server.take_connection()
		var packet = peer.get_packet()
		var packet_str = packet.get_string_from_utf8()
		#print("Received data: %s" % [packet_str])
		# Reply so it knows we received the message.
		peer.put_packet(packet)
		
		var positions = packet_str.split(",")
		var x = float(positions[0])
		var y = -float(positions[1])
		var z = -float(positions[2])
		var a = float(positions[3])
		var p = float(positions[4])
		
		global_position = Vector3(x,y,z)
		global_rotation_degrees = Vector3(90+p,0,0)
		rotate(Vector3(0,0,1),deg_to_rad(90+a))

	for i in range(0, peers.size()):
		pass # Do something with the connected peers.
