class Port:
    def __init__(self, config):
        self._name = config["name"]
        self._queues = {queue_name: queue.Queue(maxsize=1) for queue_name in ["input", "output"]}
        
        # Implement any additional functionality or initialization here

    def set_router(self, router):
        self._router = router

    def send_data(self, data: Union[DataType1, DataType2], destination: str) -> None:
        """
        Sends the provided data to the specified destination through the router.

        :param data: The data to be sent. Can be of type DataType1 or DataType2.
        :type data: Union[DataType1, DataType2]
        :param destination: The destination to send the data to.
        :type destination: str
        """
        if not self._is_destination_valid(destination):
            raise InvalidDestinationError("Invalid destination provided.")
        
        formatted_data = self._format_data(data)

        self._router.send_data(formatted_data, destination)
    
    def _is_destination_valid(self, destination: str) -> bool:
        """
        Checks if the provided destination is valid based on the available destinations in the router.

        :param destination: The destination to check.
        :type destination: str
        :return: True if the destination is valid, False otherwise.
        """
        return destination in self._router.available_destinations