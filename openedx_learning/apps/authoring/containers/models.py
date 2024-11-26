from django.db import models

from openedx_learning.apps.authoring.publishing.models import (
    PublishableEntity,
    PublishableEntityVersion,
)
from ..publishing.model_mixins import (
    PublishableEntityMixin,
    PublishableEntityVersionMixin,
)


class ContainerEntity(PublishableEntityMixin):
    """
    NOTE: We're going to want to eventually have some association between the
    PublishLog and Containers that were affected in a publish because their
    child elements were published.
    """

    pass


class ContainerEntityVersion(PublishableEntityVersionMixin):
    """
    A version of a ContainerEntity.

    By convention, we would only want to create new versions when the Container
    itself changes, and not when the Container's child elements change. For
    example:

    * Something was added to the Container.
    * We re-ordered the rows in the container.
    * Something was removed to the container.
    * The Container's metadata changed, e.g. the title.
    * We pin to different versions of the Container.

    The last looks a bit odd, but it's because *how we've defined the Unit* has
    changed if we decide to explicitly pin a set of versions for the children,
    and then later change our minds and move to a different set. It also just
    makes things easier to reason about if we say that defined_list never
    changes for a given ContainerEntityVersion.
    """

    container = models.ForeignKey(
        ContainerEntity,
        on_delete=models.CASCADE,
        related_name="versions",
    )


class ContainerMember(models.Model):
    """
    Each EntityListRow points to a PublishableEntity, optionally at a specific
    version.

    There is a row in this table for each member of an EntityList. The order_num
    field is used to determine the order of the members in the list.
    """

    container_entity_version = models.ForeignKey(ContainerEntityVersion, on_delete=models.CASCADE)
    order_num = models.PositiveIntegerField()
    entity = models.ForeignKey(PublishableEntity, on_delete=models.RESTRICT)
    version = models.ForeignKey(
        PublishableEntityVersion,
        on_delete=models.RESTRICT,
        null=True,
        related_name="version",
    )

class Selector(PublishableEntityMixin):
    """
    A Selector represents a placeholder for 0-N PublishableEntities

    A Selector is a PublishableEntity.

    We'll probably want some kind of SelectorType hierarchy like we have
    for ComponentType. But it's not necessarily exclusive–I haven't really
    decided whether something can be both a Component *and* a
    Selector, and doing so _might_ be convenient for shoving in XBlock
    UI. In any case, I don't want to close the door on it.

    A Selector has versions.
    """
    pass


class SelectorVersion(PublishableEntityVersionMixin):
    """
    A SelectorVersion doesn't have to define any particular metadata.

    Something like a SplitTestSelectorVersion might decide to model its children
    as Variants, but that's up to individual models. The only thing that this
    must have is a foreign key to Selector, and Variants that point to it.
    """
    selector = models.ForeignKey(Selector, on_delete=models.RESTRICT)


class Variant(ContainerEntityVersion):
    """
    A SelectorVersion should have one or more Variants that could apply to it.

    Variants could be created and stored as part of content (e.g. two different
    A/B test options), or a Variant could be created on a per-user basis–e.g. a
    randomly ordered grouping of ten problems from a set of 100.

    We are going to assume that a single user is only mapped to one Variant per
    Selector, and that mapping will happen via a model in the ``learning``
    package).
    """
    selector_version = models.ForeignKey(SelectorVersion, on_delete=models.RESTRICT)
