"""init23

Revision ID: df7cfb34995a
Revises: 73d58d48ea04
Create Date: 2025-04-12 23:35:08.202772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'df7cfb34995a'
down_revision: Union[str, None] = '73d58d48ea04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    
    # 2. Создаем таблицу employee без FK на department
    op.create_table(
        'employee',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=255), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        # Оставляем FK на users.id, т.к. таблица users уже создана
        sa.ForeignKeyConstraint(['employee_id'], ['users.id']),
        sa.PrimaryKeyConstraint('employee_id')
    )
    
    # 3. Создаем таблицу enterprise без FK на employee (поле boss_id)
    op.create_table(
        'enterprise',
        sa.Column('enterprise_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('boss_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('enterprise_id')
    )
    
    # 4. Создаем таблицу department, с FK на enterprise (без циклической зависимости)
    op.create_table(
        'department',
        sa.Column('department_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('enterprise_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['enterprise_id'], ['enterprise.enterprise_id']),
        sa.PrimaryKeyConstraint('department_id')
    )
    
    # 5. Создаем таблицу document
    op.create_table(
        'document',
        sa.Column('document_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('enterprise_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'signed', name='documentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['enterprise_id'], ['enterprise.enterprise_id']),
        sa.ForeignKeyConstraint(['sender_id'], ['employee.employee_id']),
        sa.PrimaryKeyConstraint('document_id')
    )
    
    # 6. Добавляем отсутствующие внешние ключи (для разрыва цикла)
    op.create_foreign_key(
        'fk_employee_department',
        source_table='employee',
        referent_table='department',
        local_cols=['department_id'],
        remote_cols=['department_id']
    )
    op.create_foreign_key(
        'fk_enterprise_boss',
        source_table='enterprise',
        referent_table='employee',
        local_cols=['boss_id'],
        remote_cols=['employee_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Сначала удаляем внешние ключи, добавленные отдельно
    op.drop_constraint('fk_enterprise_boss', 'enterprise', type_='foreignkey')
    op.drop_constraint('fk_employee_department', 'employee', type_='foreignkey')
    
    op.drop_table('document')
    op.drop_table('department')
    op.drop_table('enterprise')
    op.drop_table('employee')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_table('users')
