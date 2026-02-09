class Orchestrator:
    def __init__(self, ingestions=None, transformations=None, analytics=None):
        """
        :param ingestions: lista de ingestors
        :param transformations: lista de transformaciones
        :param analytics: componente de analítica
        """

        self.ingestions = ingestions or []
        self.transformations = transformations or []
        self.analytics = analytics

    def run(self):
        """Ejecuta todo el pipeline: ingestions → transformations → analytics."""
        for ingestion in self.ingestions:
            # Extraer datos
            ingestion.run()

        # Transformations
        for transformation in self.transformations:
            transformation.run()

        # Analytics
        if self.analytics:
            self.analytics.run()

    def add_ingestion(self, ingestion):
        self.ingestions.append(ingestion)

    def add_transformation(self, transformation):
        self.transformations.append(transformation)

    def set_analytics(self, analytics):
        self.analytics = analytics
