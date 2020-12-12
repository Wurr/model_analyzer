# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from model_analyzer.record.record import Record
from collections import defaultdict
import itertools


class RecordAggregator:
    """
    Stores a collection of Record objects.
    """
    def __init__(self):
        self._records = defaultdict(list)

    def insert(self, record):
        """
        Insert a record into the RecordAggregator

        Parameters
        ----------
        record : Record
            A record to be inserted
        """

        if isinstance(record, Record):
            record_type = type(record)
            self._records[record_type].append(record)
        else:
            raise TritonModelAnalyzerException(
                "Can only add objects of type 'Record' to RecordAggregator")

    def add_key(self, record_type, records):
        """
        Adds or replaces all the records of a given record_type with the new
        records

        Parameters
        ----------
        record_type : Record
            record_type to add to the records.
        records : list
            List of new records to be added.
        """

        self._records[record_type] = records

    def filter_records(self, record_types=None, filters=None):
        """
        Get records that satisfy the given list of criteria.

        Parameters
        ----------

        record_types : list of types of Records
            the types of the records we are
            imposing the filter criteria on.

        filters : list of callables
            conditions that determine whether
            a given record should be returned.
            If no filters specified, all records
            of types specified by record_types will be
            returned.
            Note : This must be of the same length
                   as the list of record_types, or omitted.

        Returns
        -------
        RecordAggregator
            Returns a new RecordAggregator containing the filtered
            records
        """

        filtered_records = RecordAggregator()
        if not record_types and not filters:
            for record_type, records in self._records.items():
                filtered_records.add_key(record_type, records)
            return filtered_records

        if record_types and not filters:
            try:
                for record_type in record_types:
                    filtered_records.add_key(record_type,
                                             self._records[record_type])
                return filtered_records
            except KeyError as k:
                raise TritonModelAnalyzerException(
                    f"Record type '{k.header()}' not found in this RecordAggregator"
                )
        if filters and not record_types:
            raise TritonModelAnalyzerException(
                "Must specify the record types corresponding to each filter criterion."
            )
        if len(record_types) != len(filters):
            raise TritonModelAnalyzerException(
                "Must specify the same number of record types as filter criteria."
            )

        # Remove records that do not satisfy criteria
        for h, f in zip(record_types, filters):
            for record in self._records[h]:
                if f(record):
                    filtered_records.insert(record)

        return filtered_records

    def groupby(self, record_type, groupby_criteria, reduce_func=max):
        """
        Group all the records of a certain type together if they have the
        same value for a given groupbby criteria.

        Parameters
        ----------
        record_type : Record
            A record type
        groupby_criteria : callable
            This callable will receive a single record as the argument and
            must return the value that will be used for groupby
        reduce_func : callable
            A function to apply on the group of records

        Returns
        -------
        dict
            A dictionary where the keys are the unique values returned by
            groupby_criteria and the values are the aggregated records.
        """

        records = self.filter_records(record_types=[record_type]).get_records()
        field_values = set()
        for record in records[record_type]:
            field_values.add(groupby_criteria(record))

        groupby_result = {}
        for field_value in field_values:
            aggregated_result = self.filter_records(
                record_types=[record_type],
                filters=[
                    lambda record: groupby_criteria(record) == field_value
                ]).aggregate(record_types=[record_type],
                             reduce_func=reduce_func)
            groupby_result[field_value] = aggregated_result[record_type]

        return groupby_result

    def record_types(self):
        """
        Returns
        -------
        list of str
            a list of the types of records in this
            RecordAgrregator
        """

        return list(self._records)

    def total(self, record_type=None):
        """
        Get the total number of records in
        the RecordAggregator

        Parameters
        ----------
        record_type : a class name of type Record
            The type of records to count,
            if None, count all types

        Returns
        -------
        int
            number of records in
            the RecordAggregator
        """

        if record_type:
            if record_type not in self._records:
                raise TritonModelAnalyzerException(
                    f"Record type '{record_type.header()}' not found in this RecordAggregator"
                )
            return len(self._records[record_type])
        return sum(len(self._records[k]) for k in self._records)

    def aggregate(self, record_types=None, reduce_func=max):
        """
        Parameters
        ----------
        record_types : List of Record types
            The type of records to aggregate.
            If None, aggregates all records

        reduce_func : callable
            takes as input a list of values
            and returns one

        Returns
        -------
        dict
            keys are requested record types
            and values are the aggregated values
        """

        aggregated_records = {}
        if not record_types:
            record_types = self.record_types()
        for record_type in record_types:
            values = []
            for record in self._records[record_type]:
                values.append(record.value())
            aggregated_records[record_type] = reduce_func(values)
        return aggregated_records

    def get_records(self):
        """
        Get all the records.

        Returns
        -------
        dict
            A dictionary where the keys are record types and the values are
            an array of records with the specified type
        """

        return self._records

    def _flatten_records(self, records):
        """
        Flatten the records array by joining all the arrays together.
        """

        return list(itertools.chain.from_iterable(records))
