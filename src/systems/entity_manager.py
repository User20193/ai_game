class EntityManager:
    def __init__(self):
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def update(self, dt):
        for entity in self.entities:
            entity.update(dt)

    def render(self, surface, camera):
        for entity in self.entities:
            entity.render(surface, camera)
